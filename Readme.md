# IS MUNI QDEFX to SQL

This project is no longer maintained and serves only as a time capsule. This simple Python utility was created as part of the standalone headless-cms EDU CMS project, and the ISMUNI test set data is no longer used by the CMS.

The purpose of the utility is to parse and process *.QDEFX files (the internal format of IS MUNI for online test answer sheets) and to generate a basic SQL structure for test questions, answers, and their relationships for the TestQuestion framework Python microservice within the educational CMS backend system.

## Dependencies:

**xmltodict**
```
pip install xmltodict
```

## Run Example:

```bash
python main.py -db cms -f vse.qdefx
```

# Note

Do whatever you want with this! I dont care. :)
