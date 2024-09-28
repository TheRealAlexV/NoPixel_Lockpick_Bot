# HotwireBot

A Python script that uses computer vision to automate the hotwire/Lockpick circle minigame in QBCore servers.

## Description

HotwireBot uses computer vision techniques to detect the game state and automatically perform the required actions, making the hotwiring process more efficient and consistent.

## Features

- Automated detection and interaction with the hotwire minigame
- Configurable screen zone for different resolutions
- HSV color space calculations for improved accuracy

## Dependencies

All required dependencies are listed in the [requirements.txt](requirements.txt) file. To install them, run:

```
pip install -r requirements.txt
```

## Usage

To run the HotwireBot, use the following command:

```
python HotwireBot.py
```

Make sure you have the game window open and the hotwire minigame visible on your screen before running the script.

## Configuration

You will need to update the screen zone in the `HotwireBot.py` file to match your screen resolution. Locate the following lines in the script and adjust the values as needed:

```python
zone = {"top": 647, "left": 1207, "width": 145, "height": 145}
```

These values define the area of your screen where the hotwire minigame appears. You may need to experiment with these values to find the correct zone for your setup.

## HSV Calculator

The repository includes an `HSV_Calculator.ipynb` Jupyter notebook. This tool can help you calculate the optimal HSV (Hue, Saturation, Value) color ranges for detecting game elements if you need to fine-tune the bot's performance.

## Disclaimer

This bot is intended for educational and testing purposes only. Using automated tools on live RP servers may violate the server's rules. Always check and comply with the server's policies before using any automated tools.

## Contributing

Contributions to improve the bot are welcome. Please feel free to submit issues or pull requests to enhance its functionality or documentation.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.