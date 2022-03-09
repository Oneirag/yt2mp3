# Generate .ts files 
QT standard file extension for translations is `.ts` format, but in order to easily edit them with PyCharm here will be generated with `.xml` extension. 

**Important**: lupdate is not able to extract references to `translate` function calls, only to deprecated `tr` calls, so `pyupdate6` must be used.

`pylupdate6 browser.py dialog_progress.py -ts i18n/es_ES.xml -no-obsolete`

# Compile .xml to .qm files 

Needs QT 6xx installed. It will generate a `.xml.qm` file

It also copies es_ES to en_ES (to make it work in macos)

`../../../Qt/6.2.3/macos/bin/lrelease i18n/es_ES.xml;
cp i18n/es_ES.xml.qm i18n/en_ES.xml.qm`