from django import forms


class TextInput(forms.TextInput):
    template_name = "turtlemail/widgets/text_input.jinja"

    def __init__(self, *args, **kwargs):
        additional_classes = kwargs.get("attrs", {}).get("class", "")
        kwargs["attrs"] = {"class": f"input input-bordered #{additional_classes}"}
        super(forms.TextInput, self).__init__(*args, **kwargs)
