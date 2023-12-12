pip install -U rsconnect-python
rsconnect add -i --server https://connect.doit.wisc.edu --name wise --api-key $POSIT_API_KEY
rsconnect deploy streamlit -n wisc --entrypoint api:app .