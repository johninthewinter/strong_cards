# Security

The public repository intentionally excludes raw private-repository transcripts,
absolute workstation paths, credentials, machine identifiers, and proprietary
source code. The local `.private-inputs/` directory is ignored by Git.

`make verify-publication` scans the current tracked files, every blob reachable
from Git history, commit metadata, remote URLs, and the private-archive boundary.
It rejects credential formats, personal home paths, temporary machine paths,
email addresses in published files, network identifiers, private-key material,
tracked secret-bearing filenames, and non-noreply commit addresses.

If you find private data in a tracked file, do not open a public issue containing
the data. Contact the repository owner privately and identify only the affected
path.
