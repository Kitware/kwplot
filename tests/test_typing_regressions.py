def test_video_array_inputs_shape():
    import numpy as np

    from kwplot.video_writer import VideoArrayInputs

    inputs = VideoArrayInputs(np.zeros((2, 3, 5, 3), dtype=np.uint8))
    inputs._ensure_input_dsize()
    assert inputs.input_dsize == (5, 3)


def test_label_manager_copy():
    from kwplot.managers import LabelManager

    manager = LabelManager({'foo': 'bar'})
    copied = manager.copy()
    assert copied._dict_mapper == manager._dict_mapper
    assert copied._dict_mapper is not manager._dict_mapper


def test_palette_copy():
    from kwplot.util_seaborn import Palette

    palette = Palette({'foo': 'red'})
    copied = palette.copy()
    assert copied == palette
    assert copied is not palette
