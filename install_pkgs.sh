#!/bin/bash

sudo apt-get install -y xorg slim i3 j4-dmenu-desktop playerctl keychain feh\
                        scrot mupdf jmtpfs galculator vifm rtorrent alsa-utils\
                        xarchiver terminator pulseaudio git htop jq dnsutils\
                        pass tmux unison firefox-esr thunderbird sudo vim-gtk3\
                        vlc libreoffice network-manager-gnome\
                        network-manager-openvpn-gnome smbclient ntfs-3g anacron\
                        ripgrep exuberant-ctags curl gimp bash-completion fd-find\
                        colordiff ncdu

 # direnv httpie tldr xserver-xorg-input-synaptics

hostname=`hostname`
if [[ "$hostname" == "yoga" || $hostname == "laptop" ]]; then
  sudo apt-get install -y xbacklight

  if [[ "$hostname" == "yoga" ]]; then
    sudo apt-get install -y firmware-misc-nonfree
  fi
fi

if [[ "$hostname" == "jaylen" ]]; then
  sudo apt-get install -y numlockx
fi
