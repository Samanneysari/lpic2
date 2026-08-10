# Contributing

Thank you for improving this LPIC-2 guide.

## Writing rules

- Use simple, direct English.
- Explain a term before using it in a complex procedure.
- Map content to an official LPIC-2 objective.
- Use realsam.ir and its subdomains in service examples.
- Use RFC 1918 private addresses for labs.
- Use RFC 5737 or RFC 3849 documentation addresses for public examples.
- State the distribution and version when a command is distribution-specific.
- Validate configuration before reload.
- Prefer reload over restart when supported.
- Add a warning before destructive storage, firewall, bootloader, or security commands.
- Never include a real password, private key, token, or personal address.
- Do not recommend disabling SELinux or AppArmor.
- Link to primary official documentation.

## Markdown

Use headings in order and one blank line around lists and code blocks. Use fenced code blocks with a language.

Run:

~~~bash
python3 scripts/check_docs.py
~~~

## Content change checklist

1. Check the current LPI objective.
2. Confirm commands against current upstream or distribution documentation.
3. Add a safe example and a validation command.
4. Add troubleshooting evidence.
5. Update labs or practice questions when coverage changes.
6. Run the documentation checker.
7. Review the rendered Markdown.
