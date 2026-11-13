<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/hero-dark-narrow.svg">
  <source media="(max-width: 600px)" srcset="assets/hero-light-narrow.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img src="assets/hero-light.svg" width="100%" alt="Trevor Antony, full-stack software engineer working on AI and UI/UX.">
</picture>

Full-stack software engineer in Nairobi, building AI products end to end, with a particular eye for frontend and UI/UX. I design and ship the interface people touch and everything behind it: React and TypeScript design systems, Python services and data pipelines, and AI assistants that act with human approval.

**Frontend and UI/UX** · design systems and component frameworks, YAML-driven interfaces, accessible dashboards, dark and light theming, phone-first layouts.<br>
**AI** · agent tooling with approval flows, model routing and budgets, chat that renders live data views.<br>
**Full stack** · FastAPI and SQLAlchemy services, workflow engines, PostgreSQL, Docker, Playwright end-to-end tests.

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/activity-dark-narrow.svg">
  <source media="(max-width: 600px)" srcset="assets/activity-light-narrow.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <img src="assets/activity-light.svg" width="100%" alt="Daily candlestick chart of Trevor Antony's GitHub contributions over the last 120 days, with daily volume and a seven-day average.">
</picture>

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/private-dark-narrow.svg">
  <source media="(max-width: 600px)" srcset="assets/private-light-narrow.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/private-dark.svg">
  <img src="assets/private-light.svg" width="100%" alt="Merged pull requests per month since October 2021, private and public, shown as totals only.">
</picture>

<details>
<summary><b>How an AI change reaches the data</b></summary>

```mermaid
flowchart LR
  P[Person] -->|asks| C[Chat UI]
  C --> R[Router: task, sensitivity, budget]
  R --> M[Model]
  M -->|proposes a change| A{Approval card}
  A -->|approved| V[Verb with its policy]
  V --> D[(Database)]
  V -->|receipt| C
  A -->|declined| C
```

</details>

<p>
<!-- open-source:start -->
<sub>MERGED PULL REQUESTS IN PUBLIC REPOSITORIES</sub><br><a href="https://github.com/openmrs/openmrs-esm-stock-management-app">openmrs-esm-stock-management-app</a> <sub>11</sub> · <a href="https://github.com/openmrs-archive/openmrs-esm-clinical-views-builder">openmrs-esm-clinical-views-builder</a> <sub>2</sub> · <a href="https://github.com/openmrs/openmrs-esm-form-engine-lib">openmrs-esm-form-engine-lib</a> <sub>1</sub> · <a href="https://github.com/UCSF-IGHS/openmrs-esm-ohri">openmrs-esm-ohri</a> <sub>1</sub>
<!-- open-source:end -->
</p>

Before this I worked on health software: OpenMRS 3 microfrontends and DUFT, a data analysis tool for health programmes.

<sub>[Portfolio](http://portfolio-psi-liart-96.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/trevor-omondi-142561262/) · trvromondi@gmail.com</sub>
