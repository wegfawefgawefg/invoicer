# invoicer

simple invoice generating tool

## Make New Identity

run new_identity.py

sample interaction

```bash
Enter a unique identifier for the new identity (e.g., 'mr_man', 'bla_and_co'): mr_man
Name [Your Company Name]: Mr. Man
Address (use '\n' for new lines) [1234 Street Address
City, State, ZIP]: 9876 New Avenue\nNew City, State, ZIP
Phone [123-456-7890]: 555-123-4567
Email [info@yourcompany.com]: mr.man@example.com
Identity 'mr_man' has been saved to identities/mr_man.yaml.
```

## Make New Invoice

run new_invoice.py
python3.11 invoicer.py --biller identities/mr_man.yaml --billee identities/bla_and_co.yaml --items items/sample_items.yaml
