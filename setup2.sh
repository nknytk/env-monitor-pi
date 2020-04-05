sudo modprobe i2c-dev
sudo mknod /dev/i2c-1 c 89 1

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt

git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
python ./setup.py build
python ./setup.py install
rm -rf Adafruit_Python_SSD1306

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT/
python setup.py install
cd ../
rm -rf Adafruit_Python_DHT

mkdir -p log

echo 'finally, write this to /etc/rc.local'
echo 'cd /${distribution-dir} && ./run.sh'
