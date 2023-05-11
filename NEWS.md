# Grumble Releases

# Grumble 1.1 (10-May-2023)

* Added a new `GRUMBLE_MERGE_THREADS=1` environment variable that will merge
  all thread logs into the main Grumble log files.

* Added thread information to the log files.

* Fixed crashes that could occur when running in threads, depending on
  initialization order.

* Fixed a bug in log file path building that could lead to a crash in some
  executables.


# Grumble 1.0 (16-October-2022)

* Initial public release of Grumble.
