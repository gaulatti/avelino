# Qt String identity diagnostic

This standalone probe compares Qt's canonical NFD equality with the preserved
native Swift String pairs. It uses Qt Core 6.8.3 exactly and does not implement
Avelino's selection behavior. The recorded run used Linux ARM64 and the toolchain
image identified in the parent `tooling-provenance.json`.

From the repository root, with Qt 6.8.3 available at `/opt/qt`:

```sh
cmake -S evidence/reference-investigations/radio-20261016/linux-normalization-probe -B /tmp/avelino-radio-normalization -DCMAKE_PREFIX_PATH=/opt/qt
cmake --build /tmp/avelino-radio-normalization
/tmp/avelino-radio-normalization/qt-string-identity evidence/reference-investigations/radio-20261016/native-string-identity.json /tmp/avelino-radio-normalization/result.json
```

The preserved result is `../qt-string-identity.json`: 17 disagreements among
13,762 pairs. The process returns zero when it writes its diagnostic successfully;
that exit code does not claim equivalent String identity. Inspect the report's
`mismatches` and individual `qtCanonicalEqual`/`equal` fields. Keep new output
outside this evidence directory; ordinary verification never updates the record.
