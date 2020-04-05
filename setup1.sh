for pkg in python3-dev python3-venv build-essential git python3-rpi.gpio libffi-dev libopenjp2-7 libtiff5; do
  pkg_install_status=$(dpkg -l ${pkg} | grep "${pkg}" | awk '{print $1}')
  if [ "${pkg_install_status}" != "ii" ]; then
    sudo apt install -y ${pkg}
  fi
done

if [ $(grep -c 'enable_uart=1' /boot/config.txt) -lt 1 ]; then
  echo 'enable_uart=1' | sudo tee -a /boot/config.txt
fi
sudo sed -i "s/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/" /boot/config.txt
