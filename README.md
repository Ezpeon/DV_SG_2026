# How Alternative Investments Diverged Between Institutions and Households

An interactive Streamlit poster comparing household and institutional participation in alternative investments, and the performance of some alternative assets against the S&P 500.

## To run locally:

Install requirements:
```bash
pip install -r app_requirements.txt
```

Run (from the `webapp` directory, so the local `.streamlit/config.toml` is picked up):
```bash
cd webapp
streamlit run app.py
```

## To build and run on Docker:

```bash
docker build -t dv2026 .
docker run --rm -p 8501:8501 dv2026
```

## License

MIT License, see [LICENSE](LICENSE).