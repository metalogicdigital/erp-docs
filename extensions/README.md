# Vendored Sphinx extensions

The theme and directives in this folder come from the
[Odoo documentation](https://github.com/odoo/documentation) project, branch `17.0`,
© Odoo S.A., licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
(full text in `LICENSE-odoo-documentation`). Under the same licence, our changes to them
are shared alike.

| Folder | Purpose |
|---|---|
| `odoo_theme` | The HTML theme: layout, SCSS, JavaScript for the menu and page TOC |
| `custom_admonitions` | `example` and `exercise` admonitions, `dfn` role |
| `cards` | `cards` / `card` directives |
| `spoilers` | `spoiler` directive |
| `graphviz_placeholder` | Fallback when `dot` is not installed |

Changes made here:

- Removed the Odoo logos and favicon from `odoo_theme/static/img`.
- Removed the logo easter egg from `odoo_theme/static/style.scss`.

Branding, header, footer and homepage templates are overridden in `_templates/` rather than
edited here, so the theme can be refreshed from upstream. Odoo is a trademark of Odoo S.A.;
this site is not affiliated with or endorsed by Odoo S.A.
