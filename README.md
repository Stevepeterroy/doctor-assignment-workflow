# Doctor Assignment Workflow — CSR Project

An educational LangGraph notebook that collects a fictional intake, routes it to a ward, and assigns the first active doctor from a local roster. It demonstrates typed graph state, conditional edges, an LLM adapter and session-local availability updates.

## Run the notebook

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/jupyter notebook
```

Open `doctor assigning.ipynb`. The notebook was designed for Google Colab and uses its file-upload helper. In Colab, upload a local copy of `doctors.example.csv` named `doctors.csv`. For local Jupyter, skip the Colab upload cell and put `doctors.csv` beside the notebook. Enter your own Groq key at the hidden prompt; `.env.example` documents the variable name but is not loaded automatically. A supported Groq model and network access are required for the LLM path.

Roster columns are `doctor_name`, `ward`, `status`. Ward labels are `general`, `emergency`, `mental_health`; available doctors have status `active`. The supplied roster is synthetic. No real patient data, doctor roster, saved API keys or notebook outputs are included.

## Limits

This is a workflow demonstration, not a clinical triage system. Keyword rules and LLM classifications are unvalidated and can misroute a case. Use fictional examples only. Availability is changed in notebook memory and is not safe for concurrent scheduling. There is no live hospital integration. Live Groq calls were not verified during publication.

## Reproducible local scheduling demo

The original Colab notebook is retained. A separate standard-library CLI now demonstrates durable, atomic fictional availability without Groq or patient data:

```sh
python workflow.py --roster doctors.example.csv --route general
python -m unittest discover -v
```

Use `--request-id UUID` to retry the same request safely. Unknown/free-form routing output requires human review; no default general-ward fallback is applied by this CLI. It does not implement clinical classification, real scheduling, or a tested live LLM integration. No actual people should be entered. The notebook itself remains session-local; use this CLI to demonstrate the improved persistence contract.

## Local interface

Install requirements-demo.txt and run `streamlit run app.py`. The interface calls the same tested business functions as the CLI. This is a local educational demonstration.
