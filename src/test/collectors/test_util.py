import pytest
from pyfakefs.fake_filesystem_unittest import TestCase

from palworld_exporter.collectors.util import find_save_directory


class UtilTestCase(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
    
    def test_valid_direct_path(self):
        dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95"
        self.fs.create_dir(dir)
        self.fs.create_file(f"{dir}/Level.sav")

        found = find_save_directory(dir)
        assert found == dir
    
    def test_valid_indirect_path(self):
        dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95"
        self.fs.create_dir(dir)
        self.fs.create_file(f"{dir}/Level.sav")

        found = find_save_directory("/Pal")
        assert found == dir

    def test_valid_has_settings_ini(self):
        dir = "/Pal"
        save_dir = "/Pal/Saved/SaveGames/0/2FAAC44DFD3E4DA18C418EE1F577A560"
        self.fs.create_dir(save_dir)
        self.fs.create_file("/Pal/Saved/Config/LinuxServer/GameUserSettings.ini", contents="""
[/Script/Pal.PalGameLocalSettings]
AudioSettings=(Master=0.500000,BGM=1.000000,SE=1.000000,PalVoice=1.000000,HumanVoice=1.000000,Ambient=1.000000,UI=1.000000)
GraphicsLevel=None
DefaultGraphicsLevel=None
bRunedBenchMark=False
bHasAppliedUserSetting=False
DedicatedServerName=2FAAC44DFD3E4DA18C418EE1F577A560
                            """)
        
        found = find_save_directory(dir)
        assert save_dir == found
    

    
    def test_invalid_no_settings_ini(self):
        dir = "/empty/directory"
        self.fs.create_dir(dir)
        
        with pytest.raises(FileNotFoundError):
            find_save_directory(dir)
