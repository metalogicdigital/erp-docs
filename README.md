# MetaLogic ERP Docs

Industry case studies and delivery practices for MetaLogic's Odoo implementations, published at
https://metalogicdigital.github.io/erp-docs/.

The site is built with Sphinx and a theme adapted from the Odoo documentation (see
`extensions/README.md`). Every push to `main` is built and deployed to GitHub Pages by
`.github/workflows/pages.yml`; pull requests are built but not deployed.

## Layout

```
content/
  index.rst                  site root (rendered by _templates/layout_templates/homepage.html)
  case_studies.rst           one card per industry
  case_studies/<industry>.rst      overview page of a case study
  case_studies/<industry>/*.rst    its detail pages
  delivery.rst, delivery/*.rst     how we deliver (SDLC, CI/CD, defect pipeline)
_templates/layout_templates/ header, footer and homepage overrides
static/                      site CSS and images
extensions/                  vendored theme and directives
```

## Adding a case study

1. Create `content/case_studies/<industry>.rst` (copy the structure of `retail.rst`: key figures,
   the customer, the challenge, the solution at a glance, and a toctree of detail pages).
2. Add detail pages under `content/case_studies/<industry>/`.
3. Add a `card` and a toctree entry for it in `content/case_studies.rst`.
4. Optionally add it to the industries list in `_templates/layout_templates/homepage.html`.

Customers are anonymised. Do not publish customer names, people, IP addresses, credentials or
internal hostnames.

## Building locally

Python 3.10 and graphviz (`dot`) are needed:

```sh
pip install -r requirements.txt
sh build.sh            # output in _build/html
```

Without Python installed, use Docker:

```sh
docker run --rm -v "$PWD:/docs" -w /docs python:3.10-slim \
  sh -c "pip install -q -r requirements.txt && sh build.sh"
```

Diagrams render as placeholders when `dot` is missing; CI installs it.

## Writing style

Pages use reStructuredText as in the Odoo documentation: `.. note::`, `.. tip::`, `.. example::`,
`.. seealso::`, `.. tabs::`, `.. cards::`, definition lists and `.. graphviz::` diagrams. The
build runs with warnings as errors.
