# Unit tests for the internal ragged-list -> data.frame helper. No network.

test_that("ragged lists are filled with NA", {
  x <- datasinking:::.list_to_df(list(
    list(a = "1", b = "2"),
    list(a = "3", c = "4")
  ))
  expect_s3_class(x, "data.frame")
  expect_equal(names(x), c("a", "b", "c"))
  expect_equal(x$a, c("1", "3"))
  expect_true(is.na(x$b[2]))
  expect_true(is.na(x$c[1]))
})

test_that("empty input gives an empty data.frame", {
  x <- datasinking:::.list_to_df(list())
  expect_s3_class(x, "data.frame")
  expect_equal(nrow(x), 0)
})

test_that("all fields present in every row are preserved", {
  x <- datasinking:::.list_to_df(list(
    list(id = 1, title = "a"),
    list(id = 2, title = "b")
  ))
  expect_equal(names(x), c("id", "title"))
  expect_equal(x$id, c("1", "2"))
})
