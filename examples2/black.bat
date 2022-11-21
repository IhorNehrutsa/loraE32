::pip install black
copy "%1" "%1".bak

python.exe "c:\Users\negrutsa_ii\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\local-packages\Python38\site-packages\black" "%1"

::python.exe "c:\Users\negrutsa_ii\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\black" "%1"

::python.exe "C:\Python\Python38-32\\Lib\site-packages\yapf" -vv -i "%1"

pause
