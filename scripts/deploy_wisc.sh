pip install -U rsconnect-python
rsconnect add -i --server https://connect.doit.wisc.edu --name wisc --api-key $POSIT_API_KEY
rsconnect deploy streamlit -n wisc --entrypoint app.py .