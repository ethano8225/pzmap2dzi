pushd %~dp0..
for /f "delims=" %%x in (config.txt) do set %%x
for /f "delims=" %%x in (%~dp0config_update.txt) do set %%x

%python% main.py -o test_output\html\foraging_top %common_param% %common_top_param% %foraging_top_param% foraging_top "%map_path%"
popd