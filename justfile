# Configures the Orbit profiles
configure:
    pip install git+https://github.com/chaseruskin/aquila.git@main
    orbit config --push include="$(aquila-config --config-path)"
    pip install git+https://github.com/chaseruskin/verb.git@main
    orbit config --push include="$(verb-config --config-path)"

# Run the suite of hardware simulations
test:
    orbit test

# Run the suite of tests for the software models themselves
test-sw:          
    python -m unittest discover -s sim -p "*.py"
