from pathlib import Path
import sf_channel


def test_list_and_validate_channels():
    channels = sf_channel.list_channels()
    assert len(channels) >= 1
    tgv = next(c for c in channels if c["slug"] == "the-grey-verdict")
    assert tgv["modules_present"] == 6
    assert tgv["status"] == "valid"

    val_res, val_code = sf_channel.validate_channel("the-grey-verdict")
    assert val_code == 0
    assert val_res["ok"] is True


def test_scaffold_channel(monkeypatch, tmp_path):
    # Mock ROOT channels dir to tmp_path
    monkeypatch.setattr(sf_channel, "get_channels_dir", lambda: tmp_path)
    
    # Copy _template from real repo to tmp_path
    import shutil
    real_template = Path(__file__).resolve().parent.parent / "channels" / "_template"
    shutil.copytree(real_template, tmp_path / "_template")

    res, code = sf_channel.scaffold_channel("dark-tales", name="Dark Tales", niche="Horror folklore", language="en")
    assert code == 0
    assert res["ok"] is True
    assert (tmp_path / "dark-tales").is_dir()
    for mod in sf_channel.REQUIRED_MODULES:
        assert (tmp_path / "dark-tales" / mod).exists()

    val_res, val_code = sf_channel.validate_channel("dark-tales")
    assert val_code == 0
    assert val_res["ok"] is True
