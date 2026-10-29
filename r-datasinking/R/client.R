# DataSinking R client ---------------------------------------------------
#
# A thin R client for the DataSinking API (https://datasink.ing).
# Serves full-text financial reports (annual / semi-annual / quarterly)
# as clean Markdown, addressable by document or section.
#
# Usage:
#   ds <- datasinking("YOUR_API_KEY")
#   ds$list_exchanges()
#   ds$list_stocks("szse")
#   ds$list_reports("000006.SZ")
#   ds$get_section(12345, "MD&A")


#' Create a DataSinking API client
#'
#' @param api_key Your DataSinking API key (free at <https://datasink.ing>).
#' @param base_url API base URL. Defaults to the production endpoint.
#'
#' @return A list of functions (the client). See Details.
#'
#' @details The returned client exposes:
#' \itemize{
#'   \item \code{list_exchanges()} — vector of exchange codes (e.g. \code{"szse"}).
#'   \item \code{list_stocks(exchange)} — stocks on one exchange (list of records).
#'   \item \code{list_reports(symbol, doc_type = NULL)} — report metadata for a
#'     symbol (no full text). \code{doc_type} one of annual/semiannual/q1/q3/amendment.
#'   \item \code{get_report(doc_id)} — one report's full record (includes Markdown body).
#'   \item \code{get_stock_reports(symbol, period_from = NULL, period_to = NULL,
#'     limit = 7, doc_type = NULL)} — full text of the latest reports for a symbol.
#'     \code{period_from/period_to} filter by report period (YYYY-MM-DD), not filing date.
#'     \code{limit = -1} pulls all.
#'   \item \code{list_sections(doc_id)} — section headings of a report.
#'   \item \code{get_section(doc_id, section)} — one section's record (cheaper than
#'     \code{get_report} for RAG).
#'   \item \code{submit_feedback(exchange, stock_code)} — queue a re-parse.
#'   \item \code{get_feedback_status(feedback_id)} — poll a feedback job.
#' }
#'
#' @export
datasinking <- function(api_key, base_url = "https://api.datasink.ing") {
  if (missing(api_key) || !is.character(api_key) || !nzchar(api_key)) {
    stop("api_key is required (get one free at https://datasink.ing)", call. = FALSE)
  }
  base_url <- sub("/$", "", base_url)
  ua <- httr::user_agent("datasinking-r/0.1.0")

  .raise <- function(resp) {
    status <- httr::status_code(resp)
    txt <- httr::content(resp, "text", encoding = "UTF-8")
    if (status == 429L) {
      stop("DataSinking quota exceeded (429): ", txt, call. = FALSE)
    }
    stop("DataSinking API error ", status, ": ", txt, call. = FALSE)
  }

  .get <- function(path, query = list()) {
    query$apikey <- api_key
    resp <- httr::GET(paste0(base_url, path), query = query, ua)
    if (httr::http_error(resp)) .raise(resp)
    jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"),
                       simplifyVector = FALSE)
  }

  .post <- function(path, body = list()) {
    resp <- httr::POST(paste0(base_url, path),
                       query = list(apikey = api_key),
                       body = jsonlite::toJSON(body, auto_unbox = TRUE),
                       httr::content_type_json(), ua)
    if (httr::http_error(resp)) .raise(resp)
    jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"),
                       simplifyVector = FALSE)
  }

  .fetch_all_meta <- function(params) {
    items <- list()
    page <- 1L
    repeat {
      d <- .get("/documents", c(params, list(page = page, size = 200L)))
      items <- c(items, d$items)
      total <- if (is.null(d$total)) 0 else as.numeric(d$total)
      if (length(d$items) == 0L || length(items) >= total) break
      page <- page + 1L
    }
    items
  }

  .batch_content <- function(ids) {
    if (length(ids) == 0L) return(list())
    out <- list()
    i <- 1L
    size <- 31L
    while (i <= length(ids)) {
      if (size > length(ids) - i + 1L) size <- length(ids) - i + 1L
      chunk <- ids[i:(i + size - 1L)]
      if (length(chunk) == 1L) {
        out <- c(out, list(.get(paste0("/documents/", chunk[[1]]))))
        i <- i + 1L
        next
      }
      resp <- tryCatch(.post("/documents/batch", list(doc_ids = chunk)),
                       error = function(e) e)
      if (inherits(resp, "error")) {
        if (grepl("429", conditionMessage(resp))) stop(resp)
        # 400/403 → free-tier batch too large, shrink and retry
        size <- if (size > 6L) size %/% 3L else size - 1L
        if (size < 1L) size <- 1L
        next
      }
      out <- c(out, resp$items)
      i <- i + size
    }
    out
  }

  list(
    list_exchanges = function() {
      .get("/exchanges")$exchanges
    },

    list_stocks = function(exchange) {
      .get("/stocks", list(exchange = exchange))$items
    },

    list_reports = function(symbol, doc_type = NULL) {
      params <- list(symbol = symbol)
      if (!is.null(doc_type)) params$doc_type <- doc_type
      .fetch_all_meta(params)
    },

    get_report = function(doc_id) {
      .get(paste0("/documents/", doc_id))
    },

    get_stock_reports = function(symbol, period_from = NULL, period_to = NULL,
                                 limit = 7L, doc_type = NULL) {
      params <- list(symbol = symbol)
      if (!is.null(period_from)) params$report_period_from <- period_from
      if (!is.null(period_to)) params$report_period_to <- period_to
      if (!is.null(doc_type)) params$doc_type <- doc_type
      if (identical(limit, -1L)) {
        ids <- unlist(lapply(.fetch_all_meta(params),
                             function(m) as.character(m$id)))
      } else {
        d <- .get("/documents", c(params, list(size = limit, order = "desc")))
        ids <- unlist(lapply(d$items, function(m) as.character(m$id)))
      }
      .batch_content(ids)
    },

    list_sections = function(doc_id) {
      .get(paste0("/documents/", doc_id, "/sections"))$sections
    },

    get_section = function(doc_id, section) {
      .get(paste0("/documents/", doc_id), list(section = section))
    },

    submit_feedback = function(exchange, stock_code) {
      .post("/feedback", list(exchange = exchange, stock_code = stock_code))
    },

    get_feedback_status = function(feedback_id) {
      .get(paste0("/feedback/", feedback_id))
    }
  )
}
