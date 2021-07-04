DEFAULT_BRANCH = "main"
TEST_01_MIGRATION_BRANCH = "feature/migration-test-01"  # Single merge to main
TEST_02_MIGRATION_BRANCH = (
    "feature/migration-test-02"  # Single merge to main after 01 is merged
)
TEST_03_MIGRATION_BRANCH = (
    "feature/migration-test-03"  # Merge 04 first before merging this to main
)
TEST_04_MIGRATION_BRANCH = (
    "feature/migration-test-04"  # Merge into 04 default should be 03
)
