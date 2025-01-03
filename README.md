# invoicer

simple invoice generating tool

## Usage

### Add Identities

put files in your identities folder
check the _template.yaml file for the structure

### Add Items

put files in your items folder
check the _template.yaml file for the structure

### Make New Invoice

run new_invoice.py
python3.11 invoicer.py --biller identities/mr_man.yaml --billee identities/bla_and_co.yaml --items items/sample_items.yaml --date 2022/05/01

## todo

- add optional due date
- add optional tax rate
- add optional start/end date for services
