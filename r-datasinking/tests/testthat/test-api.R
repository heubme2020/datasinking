# Integration tests against the live API. Skipped on CRAN and without a key.

test_that("ds_exchanges returns exchange codes", {
  skip_on_cran()
  skip_if(Sys.getenv("DATASINKING_API_KEY") == "", "DATASINKING_API_KEY not set")
  ex <- ds_exchanges()
  expect_type(ex, "character")
  expect_true(length(ex) > 0)
  expect_true("nyse" %in% ex || "nasdaq" %in% ex || "sse" %in% ex)
})

test_that("ds_stocks returns a data.frame", {
  skip_on_cran()
  skip_if(Sys.getenv("DATASINKING_API_KEY") == "", "DATASINKING_API_KEY not set")
  st <- ds_stocks("szse")
  expect_s3_class(st, "data.frame")
  expect_true(all(c("stock_code", "stock_name") %in% names(st)))
})

test_that("ds_documents returns metadata and total attribute", {
  skip_on_cran()
  skip_if(Sys.getenv("DATASINKING_API_KEY") == "", "DATASINKING_API_KEY not set")
  d <- ds_documents(symbol = "600519.SS", doc_type = "annual")
  expect_s3_class(d, "data.frame")
  expect_true(is.numeric(attr(d, "total")))
  expect_true("id" %in% names(d))
})

test_that("ds_report returns content and ds_sections returns titles", {
  skip_on_cran()
  skip_if(Sys.getenv("DATASINKING_API_KEY") == "", "DATASINKING_API_KEY not set")
  d <- ds_documents(symbol = "600519.SS", doc_type = "annual", size = 1)
  id <- d$id[1]
  full <- ds_report(id)
  expect_true(nchar(full$content) > 0)
  secs <- ds_sections(id)
  expect_type(secs, "character")
  expect_true(length(secs) > 0)
})

test_that("ds_batch enforces the 31-document limit", {
  skip_on_cran()
  expect_error(ds_batch(1:32), "at most 31")
})
