# Keep each earlier date catalog intact while publishing a fresh current tree.
if [[ -e artifacts/linux/date-range-catalog-installed ]]; then
  previous_date_catalog_dir="$(mktemp -d artifacts/linux/date-range-catalog-previous.XXXXXX)"
  mv artifacts/linux/date-range-catalog-installed "$previous_date_catalog_dir/catalog-installed"
fi
cp -R "$stage/date-range-catalog-evidence" artifacts/linux/date-range-catalog-installed
