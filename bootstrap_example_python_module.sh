# Get a web server
pip3 install gunicorn

# Get the core and the datamodel
pip3 install ppp_core ppp_datamodel

# Get the module
git clone https://github.com/ProjetPP/ExamplePPPModule-Python.git
# Note that you may also do: pip3 install git+https://github.com/ProjetPP/ExamplePPPModule-Python.git

# Install the module
cd ExamplePPPModule-Python
make localinstall

# Run tests
make tests

cd ..


# Make the config
echo "{
    \"debug\": true,
    \"modules\": [
        {
            \"name\": \"my_module\",
            \"url\": \"http://localhost:8001/\",
            \"coefficient\": 1
        }
    ]
}" > /tmp/ppp_core_config.json


echo "Bootstrapped! Now you just have to run in two different terminals:"
echo "  PPP_CORE_CONFIG=/tmp/ppp_core_config.json gunicorn ppp_core:app -b 127.0.0.1:8000"
echo "  gunicorn example_ppp_module:app -b 127.0.0.1:8001"
echo ""
echo "Then, you can test it from a Python shell:"
echo ">>> import requests"
echo ">>> requests.post('http://127.0.0.1:8000', data='{\"language\": \"en\", \"tree\": {\"type\": \"triple\", \"subject\": {\"type\": \"resource\", \"value\": \"you\"}, \"object\": {\"type\": \"missing\"}, \"predicate\": {\"type\": \"resource\", \"value\": \"be\"}}}').json()"
