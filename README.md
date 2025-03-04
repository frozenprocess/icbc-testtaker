# Disclaimer
This program is written for educational purposes.

# Requiremnents
Python 3
selenium

# How to run this ?
[Download ChromeDriver](https://chromedriver.storage.googleapis.com/index.html?path=105.0.5195.52/) and palced it with the script

I've used the following engine.
```
105.0.5195.52 (412c95e518836d8a7d97250d62b29c2ae6a26a85-refs/branch-heads/5195@{#853})
```

Install python requirements.
```
pip install -r requirements.txt
```

Modify `config_example.py` configurations and store it as `config.py`
```
driver_name		= "YOUR NAME"
driver_license		= "ICBC License number"
driver_password		= "ICBC portal password"
```

Next, run the script!
```
python3 main.py
```

# Optional
If you wish to run the script without watching the browser, turn on the `headless` option.
```
python3 main.py --headless true
```