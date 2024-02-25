# Documenting Aruba Central Device configuration

## Requirements
```
docx2pdf
docxcompose
icecream
pycentral
python_dateutil
sortedcontainers
```
## Installation
1. Download the zip package from github and unpack it into empty directory
2. For now create following directories in root directory:
- bom
- docx
- images
- template
3. copy docxcentral/templates/logconfig.json to template directory
4. copy docxcentral/templates/central.json to root directory
5. copy docxcentral/templates/filter.json to root directory
6. Update central.json with current Aruba Central API Authorization information

## Default directory structure

### bom/ 
Directory contains BOM (Bill of Material) word document for Aruba Central site.
BOM file is generated in Visual RF on Aruba Central site.

### docx/
Directory contains generated MS Word and PDF files.

### images/
Directory contains pictures of installed equipment. Each site has it's own directory.

Image filenames for a device start with serial number. Supported type is jpg. 

Image for Location section of the report ends with "_location.png".

### template/
Directory contains template MS Word documents used to generate final documentation.
template.dotx is a master template. It contains all formating information.

