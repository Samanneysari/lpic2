# Contributing

Thank you for improving this LPIC-2 guide.

## Required teaching structure

Every objective section must teach a beginner in this order:

1. Explain what the subject is.
2. Explain why it is used and where it fits in Linux.
3. Define new terms, processes, files, ports, and trust boundaries.
4. Describe the task as numbered steps.
5. Show the command or configuration block.
6. Put a line-by-line explanation table directly under the block.
7. Show how to validate syntax, service state, logs, and client behavior.
8. Explain common failures, recovery, and security consequences.
9. Finish with an exam checklist and a small lab.

A line-by-line table must cover every non-empty physical line. Do not write only "runs the command." Explain the program or directive, the purpose of important arguments, whether the change is temporary or persistent, the privilege required, and any destructive effect. A block containing only output may instead explain the important fields.

## Writing rules

- Use simple, direct English.
- Explain a term before using it in a procedure.
- Map content to an official LPIC-2 version 4.5 objective.
- Use realsam.ir and its subdomains in service examples.
- Use RFC 1918 private addresses for isolated labs.
- Use RFC 5737 IPv4 or RFC 3849 IPv6 addresses for public-looking examples.
- State the distribution and version when a command is distribution-specific.
- Validate configuration before reload.
- Prefer reload over restart when supported.
- Add a warning before destructive storage, firewall, bootloader, PAM, LDAP import, or security commands.
- Never include a real password, private key, token, or personal address.
- Do not recommend disabling SELinux or AppArmor.
- Link to primary official documentation.
- Preserve useful original explanations while correcting technical errors.

## Markdown rules

Use headings in order. Put one blank line around lists, tables, and code blocks. Add a language to every fenced code block. Escape pipe characters inside table cells. Check that internal links use paths relative to the current file.

Run the documentation checker:

~~~bash
python3 scripts/check_docs.py
~~~

**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>python3 scripts/check_docs.py</code> | Starts Python 3 and runs the repository documentation checker, which validates objectives, links, code fences, example domains, and unsafe patterns. |

## Content change checklist

1. Check the exact official objective and weight.
2. Confirm commands against upstream or distribution documentation.
3. Add the beginner theory before the first procedure.
4. Explain every non-empty command and configuration line directly below its block.
5. Add a safe example, a validation command, and expected evidence.
6. Add troubleshooting and security notes.
7. Update labs or practice questions when coverage changes.
8. Run the documentation checker.
9. Review the rendered Markdown.
10. Confirm that the historical file under legacy/ was not modified.
