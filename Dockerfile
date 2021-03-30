FROM joyzoursky/python-chromedriver:3.8-selenium
COPY band12_trashcan_reboot.py /usr/workspace/band12_trashcan_reboot.py
RUN pip3 install requests selenium
CMD ["python3", "-u", "/usr/workspace/band12_trashcan_reboot.py"]