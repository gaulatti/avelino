# FileInput indexed-search capability probe

This is a Linux dependency experiment, not a FileInput implementation, a chosen
desktop-provider policy, or native acceptance. All attempts remain retained:

1. The initial image lacks Python GI; the probe terminates with `ModuleNotFoundError`.
2. Installing Python GI starts Tracker 3.7.1, but the `/tmp` fixtures never enter
   the observed index. The finite observation ends with failure, not success.
3. With controlled files under `/home`, public prepared Tracker statements return
   two global filename matches and one folder filename match, versus three
   global general matches and two folder general matches. The extra general
   match is the content-only `pine-only.txt`. Trailing-slash URI folder scope
   excludes the similarly prefixed `inside-peer` directory.

The eligibility diagnostic separately reports the `/tmp` file not eligible as
an indexed folder. The successful probe retains the normal Docker security
profile and raw UPower, GLib and extractor warnings; no permission or sandbox
weakening was needed. It runs only a private session bus and explicit private
GSettings/XDG paths inside a source-free, mount-free container. It does not
change host indexing settings or override HOME.

`attempt-3/probe.py` reproduces the passing capability with Python GI, Tracker
3.7.1, its filesystem miner and text extractor installed on Ubuntu 24.04.
The recorded image is local to the verification environment; its Docker layers
are not published. The two retained Dockerfiles and pinned image identities
record construction from the prior Qt verification image. Python GI is only
a probe dependency; no application/package dependency has been added.

The queries use bound parameters. This one-word fixture does not establish
arbitrary literal/phrase handling, Unicode normalization, stemming, prefix or
substring rules, ranking, extractor coverage, index freshness or unindexed
folder policy. Default system search must not be replaced by a filename-only
scan or a fabricated index. The native observations are separately scoped in
`../../reference-investigations/file-input-search-20261020`.

Product integration still needs a supported desktop-provider decision, async
query cancellation/lifecycle, both search modes and scopes, owned input/results,
selection and type revalidation, owner callback/dismissal behavior, installed
consumer, display sessions, accessibility and native acceptance. No search UI or
backend layer is being shipped by this checkpoint.

Run `python3 scripts/verify-file-input-search.py` to audit retained facts.
