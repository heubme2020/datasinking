# DataSinking R client ---------------------------------------------------
#
# Thin wrapper around the DataSinking API (https://api.datasink.ing).
# Auth is a single `apikey` query parameter, stored in the DATASINKING_API_KEY
# environment variable by ds_set_key().

.datasinking_base_url <- "https://api.datasink.ing"

`%||%` <- function(a, b) if (is.null(a)) b else a


#' Set the DataSinking API key
#'
#' Stores the key in the `DATASINKING_API_KEY` environment variable, which all
#' other functions read automatically. Obtain a key at
#' \url{https://datasink.ing}.
#'
#' @param key Character. Your DataSinking API key.
#' @return Invisibly returns `key`.
#' @export
ds_set_key <- function(key) {
  Sys.setenv(DATASINKING_API_KEY = key)
  invisible(key)
}

.ds_key <- function() {
  key <- Sys.getenv("DATASINKING_API_KEY", unset = "")
  if (!nzchar(key)) {
    stop("No API key set. Run ds_set_key(\"your-key\") first.", call. = FALSE)
  }
  key
}

.ds_url <- function(path, query = list()) {
  query <- c(query, apikey = .ds_key())
  httr::modify_url(.datasinking_base_url, path = path, query = query)
}

.ds_get <- function(path, query = list()) {
  resp <- httr::GET(.ds_url(path, query), httr::timeout(60))
  .ds_stop_for_status(resp)
  httr::content(resp, as = "parsed", type = "application/json", encoding = "UTF-8")
}

.ds_post <- function(path, body = list()) {
  resp <- httr::POST(.ds_url(path), body = body, encode = "json", httr::timeout(60))
  .ds_stop_for_status(resp)
  httr::content(resp, as = "parsed", type = "application/json", encoding = "UTF-8")
}

.ds_stop_for_status <- function(resp) {
  if (httr::http_error(resp)) {
    status <- httr::status_code(resp)
    body <- httr::content(resp, as = "text", encoding = "UTF-8")
    stop(sprintf("DataSinking API error (HTTP %d): %s", status, body),
         call. = FALSE)
  }
  invisible(resp)
}

# Ragged list -> data.frame, filling missing keys with NA (useful for the
# documents endpoint, where metadata fields are not always all present).
# Column-wise: extract each field across items, then build the frame.
.list_to_df <- function(items) {
  if (length(items) == 0) {
    return(data.frame())
  }
  all_names <- unique(unlist(lapply(items, names), use.names = FALSE))
  cols <- lapply(all_names, function(n) {
    vapply(items, function(x) {
      val <- x[[n]]
      if (is.null(val)) NA_character_ else as.character(val)
    }, character(1))
  })
  names(cols) <- all_names
  as.data.frame(cols, stringsAsFactors = FALSE, check.names = FALSE)
}


#' List available exchanges
#'
#' Returns the exchange codes served by the API (for example `"nyse"`,
#' `"nasdaq"`, `"sse"`, `"szse"`, `"jpx"`, `"ksc"`).
#'
#' @return A character vector of exchange codes.
#' @export
ds_exchanges <- function() {
  res <- .ds_get("/exchanges")
  unlist(res$exchanges, use.names = FALSE)
}


#' List stocks on an exchange
#'
#' @param exchange Character. An exchange code from [ds_exchanges()].
#' @return A data.frame with columns such as `stock_code`, `name` and `symbol`.
#' @export
ds_stocks <- function(exchange) {
  res <- .ds_get("/stocks", list(exchange = exchange))
  .list_to_df(res$items)
}


#' List financial-report documents
#'
#' Search the document index. Pass a `symbol` (FMP-style ticker such as
#' `"AAPL"` or `"600519.SS"`) or an `exchange` + `stock_code`, optionally
#' filtered by `doc_type` (`"annual"`, `"semiannual"`, `"q1"`, `"q3"`) and/or
#' `report_period`.
#'
#' @param symbol Character or NULL. FMP-style ticker, e.g. `"AAPL"`,
#'   `"600519.SS"`, `"7203.T"`.
#' @param exchange,stock_code Character or NULL. Alternative to `symbol`.
#' @param doc_type Character or NULL. One of `"annual"`, `"semiannual"`,
#'   `"q1"`, `"q3"`.
#' @param report_period Character or NULL. Exact period, e.g. `"2023-12-31"`.
#' @param report_period_from,report_period_to Character or NULL. Inclusive
#'   period bounds, e.g. `"2023-01-01"`.
#' @param page,size Integer. Pagination (size capped by the API at 50 by
#'   default).
#' @param order `"desc"` (latest period first) or `"asc"`.
#' @param with_content Logical. If `TRUE`, return a list including each
#'   document's full Markdown `content`; if `FALSE` (default), return a
#'   data.frame of metadata only (with `total` stored as an attribute).
#' @return A data.frame (metadata) or a list (when `with_content = TRUE`).
#' @export
ds_documents <- function(symbol = NULL, exchange = NULL, stock_code = NULL,
                         doc_type = NULL, report_period = NULL,
                         report_period_from = NULL, report_period_to = NULL,
                         page = 1, size = 50, order = c("desc", "asc"),
                         with_content = FALSE) {
  order <- match.arg(order)
  q <- list(page = page, size = size, order = order,
            with_content = if (isTRUE(with_content)) 1 else NULL)
  if (!is.null(symbol))            q$symbol <- symbol
  if (!is.null(exchange))          q$exchange <- exchange
  if (!is.null(stock_code))        q$stock_code <- stock_code
  if (!is.null(doc_type))          q$doc_type <- doc_type
  if (!is.null(report_period))     q$report_period <- report_period
  if (!is.null(report_period_from)) q$report_period_from <- report_period_from
  if (!is.null(report_period_to))  q$report_period_to <- report_period_to

  res <- .ds_get("/documents", q)
  if (isTRUE(with_content)) {
    return(res$items)
  }
  df <- .list_to_df(res$items)
  attr(df, "total") <- res$total
  df
}


#' Get a single document (full text or one section)
#'
#' @param id Integer. The document id, as returned by [ds_documents()].
#' @param section Character or NULL. If given, return only that section's text
#'   (fuzzy title match, e.g. `"MD&A"`, `"risk factors"`, `"notes"`); if NULL,
#'   return the full document object.
#' @return If `section` is NULL, a list with metadata plus `content` (full
#'   Markdown). If `section` is given, a single character string.
#' @export
ds_report <- function(id, section = NULL) {
  q <- list()
  if (!is.null(section)) q$section <- section
  res <- .ds_get(sprintf("/documents/%s", id), q)
  if (!is.null(section)) {
    return(res$content %||% "")
  }
  res
}


#' List the sections of a document
#'
#' @param id Integer. The document id.
#' @return A character vector of section titles (in document order).
#' @export
ds_sections <- function(id) {
  res <- .ds_get(sprintf("/documents/%s/sections", id))
  unlist(res$sections, use.names = FALSE)
}


#' Fetch several documents in one request
#'
#' @param ids Integer vector of document ids. At most 31 per request.
#' @return A list with `count`, `missing` and `items` (each item is a document
#'   object including full Markdown `content`).
#' @export
ds_batch <- function(ids) {
  ids <- as.integer(ids)
  if (length(ids) > 31) {
    stop("The API accepts at most 31 document ids per batch.", call. = FALSE)
  }
  .ds_post("/documents/batch", list(doc_ids = ids))
}

#' Submit feedback to backfill a stock's reports
#'
#' Requests a full backfill of a stock whose reports look missing or broken,
#' and returns its current status. Idempotent: if the stock was already
#' submitted recently (within the last 127 feedback records, across all keys),
#' it returns that existing status instead of queueing a duplicate; otherwise it
#' queues a re-fetch from the IPO prospectus onward (this takes a while) and
#' returns `status = "pending"`. Poll [ds_feedback_status()] for progress.
#' Limits are separate from the reading quota: free keys once per 3 seconds,
#' 31 stocks per 7 days per key; yearly keys 3 per second, 8,191 stocks per 7
#' days.
#'
#' @param exchange Character. Exchange code, e.g. `"szse"`.
#' @param stock_code Character. Stock code from the exchange, e.g. `"002050"`.
#' @return A list with `id`, `status`, `queued` (`TRUE` = just queued) and other
#'   fields.
#' @export
ds_feedback <- function(exchange, stock_code) {
  .ds_post("/feedback", list(exchange = exchange, stock_code = stock_code))
}

#' Check the progress of a submitted feedback request
#'
#' @param feedback_id Integer. The feedback id returned by [ds_feedback()].
#' @return A list with `status` (pending / processing / done / failed) and other
#'   fields.
#' @export
ds_feedback_status <- function(feedback_id) {
  .ds_get(sprintf("/feedback/%d", as.integer(feedback_id)))
}
