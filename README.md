# No-Show Predictor

Predicting which medical appointments will be missed, built end to end the way a real ML system would be: exploration, features, a tracked model, an API, Docker and tests.

About 1 in 5 appointments in this dataset is a no-show. Each one is an empty provider slot that another patient could have used. If a clinic knew which upcoming visits were high-risk, staff could call those patients first or double-book carefully.

> Status: exploration done (Part 3). Features, model, API and Docker are in progress.

## Data

[Medical Appointment No Shows](https://www.kaggle.com/datasets/joniarroba/noshowappointments) by Joni Hoppen (Kaggle, CC BY-NC-SA 4.0). Public appointment records from Vitória, Brazil, April–June 2016.

The data isn't included in this repo. To run the notebooks, download the CSV from Kaggle and put it at `data/KaggleV2-May-2016.csv`.

## What the exploration found

Notebook: [`notebooks/01_explore.ipynb`](notebooks/01_explore.ipynb)

**The basics.** 110,527 appointments, 62,299 patients, about 6 weeks of data (2016-04-29 to 2016-06-08). No missing values. 20.2% of appointments were missed.

**Lead time is the strongest pattern so far.** Same-day appointments are almost never missed (4.6%). The no-show rate climbs as the gap between booking and appointment grows, reaching about 33% for appointments booked a month or more ahead.

**SMS reminders look harmful at first, but they aren't.** Patients who got an SMS missed 27.6% of appointments vs 16.7% for those who didn't. That's backwards from what you'd expect. The catch: SMS was only sent for appointments booked days in advance, which are missed more often anyway, and same-day patients never got one. Comparing within the same lead-time range, patients with an SMS missed *less* in every group, for example 28.1% vs 33.8% at 8–14 days and 30.2% vs 37.5% at 31+ days. The overall number was confounded by lead time. (This is an observational dataset, so it's consistent with SMS helping, not proof.)

**Many patients come back.** 24,379 patients (39%) have two or more appointments. A random train/test split would let the model see the same patient in both sets and look better than it really is. So the model will be trained on earlier weeks and tested on later weeks, and any "past no-shows" feature will only use appointments before the one being predicted.

**Data errors to clean.** 5 appointments were booked after they happened (negative lead time) and 1 patient has age -1. These get removed in the feature step.

## Run it yourself

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Abhi356213/noshow-predictor.git
cd noshow-predictor
uv sync                      # installs the exact package versions from uv.lock
# download the CSV from Kaggle into data/
```

Then open `notebooks/01_explore.ipynb` in VS Code or Jupyter and choose the project's `.venv` kernel.

## Roadmap

- [x] Exploratory analysis
- [ ] Feature engineering with a time-based split
- [ ] XGBoost model, tracked in MLflow
- [ ] FastAPI prediction endpoint
- [ ] Docker
- [ ] Tests and GitHub Actions CI
