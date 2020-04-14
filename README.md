# Dblue MLWatch

Real-time Machine Learning model monitoring with Dblue MLWatch

Fot getting started with MLWatch go to [https://mlwatch.dblue.ai](https://mlwatch.dblue.ai)

### Steps
1. Dblue MLWatch Account

	To start monitoring your machine learning models with Dblue MLWatch you need a dblue.ai account.
	If you don't already have one, please [contact support](mailto:support@dblue.ai?Subject=Need%20a%20MLWatch%20Account)

2. Installation

	```bash
	pip install dblue-mlwatch
	```

3. Initialization

	```bash
    from dblue_mlwatch import MLWatch
    
    watcher = MLWatch(
        account='account id received from dblue',
        project='project id received from dblue',
        api_key='API Key received from dblue',
        model_id="Model id received from dblue",
        model_version="Model version specified on dblue"
    )
	
	```

### Known issues:

#### Failed to install psutil on mac

```bash
# Jump to the correct folder
cd /Library/Developer/CommandLineTools/SDKs

# Move the new SDK out of the way
sudo mv MacOSX10.15.sdk MacOSX10.15.sdk.1

# Link the newer SDK to the old one
sudo ln -s MacOSX10.14.sdk MacOSX10.15.sdk

# Install psutil or the package which depends on it
pip install -U psutil

# Remove the temporary symlink we made in step 3
sudo rm MacOSX10.15.sdk

# Restore to the former state
sudo mv MacOSX10.15.sdk.1 MacOSX10.15.sdk
```