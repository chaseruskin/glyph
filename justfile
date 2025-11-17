# Configures the Orbit profiles
configure:
    pip install git+https://github.com/chaseruskin/aquila.git@main
    orbit config --push include="$(aquila-config --config-path)"
    pip install git+https://github.com/chaseruskin/verb.git@main
    orbit config --push include="$(verb-config --config-path)"

# Run the suite of hardware simulations
test:
    orbit test --keep --target goku --dut parity -- -r sim -g W=8 -g EVEN=false
    orbit test --keep --target goku --dut parity -- -r sim -g W=5 -g EVEN=true
    orbit test --keep --target goku --dut hamming_enc -- -r sim -g K=4
    orbit test --keep --target goku --dut hamming_enc -- -r sim -g K=32
    orbit test --keep --target goku --dut hamming_enc -- -r sim -g K=64
    orbit test --keep --target goku --dut hamming_dec -- -r sim -g K=4
    orbit test --keep --target goku --dut hamming_dec -- -r sim -g K=32
    orbit test --keep --target goku --dut hamming_dec -- -r sim -g K=64

# Run the suite of tests for the software models themselves
test-sw:          
    python -m unittest discover -s sim -p "*.py"
