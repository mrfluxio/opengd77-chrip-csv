import wx
from opengd77_chirp_csv_coverter import transform_channels  # Import the function

# Constants for operations
VALID_OPERATIONS = {
    "gd77": "Transform CHIRP format to OpenGD77",
    "chirp": "Transform OpenGD77 format to CHIRP"
}
DEFAULT_START_CHANNEL = 0  # Default starting channel


class FileConverterApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up the main panel
        panel = wx.Panel(self)

        # Instructions label
        instructions = wx.StaticText(panel,
                                     label="Select an operation, specify input/output files, and click Transform.")

        # Operation selection
        operation_label = wx.StaticText(panel, label="Operation:")
        self.operation_combo = wx.ComboBox(panel, choices=list(VALID_OPERATIONS.values()), style=wx.CB_READONLY)
        self.operation_combo.SetValue(list(VALID_OPERATIONS.values())[0])  # Set default operation

        # Input file selection
        input_label = wx.StaticText(panel, label="Input File:")
        self.input_text = wx.TextCtrl(panel, value="")
        input_browse_button = wx.Button(panel, label="Browse")
        input_browse_button.Bind(wx.EVT_BUTTON, self.on_browse_input)

        # Output file selection
        output_label = wx.StaticText(panel, label="Output File:")
        self.output_text = wx.TextCtrl(panel, value="")
        output_browse_button = wx.Button(panel, label="Browse")
        output_browse_button.Bind(wx.EVT_BUTTON, self.on_browse_output)

        # Transform button
        transform_button = wx.Button(panel, label="Transform")
        transform_button.Bind(wx.EVT_BUTTON, self.on_transform)

        # Layout using a grid sizer
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(instructions, pos=(0, 0), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(operation_label, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        sizer.Add(self.operation_combo, pos=(1, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(input_label, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        sizer.Add(self.input_text, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(input_browse_button, pos=(2, 2), flag=wx.ALL, border=5)
        sizer.Add(output_label, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        sizer.Add(self.output_text, pos=(3, 1), flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(output_browse_button, pos=(3, 2), flag=wx.ALL, border=5)
        sizer.Add(transform_button, pos=(4, 0), span=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Adjust layout
        sizer.AddGrowableCol(1)
        panel.SetSizerAndFit(sizer)  # Set the sizer on the panel

        # Set window properties
        self.SetTitle("File Converter")
        self.Centre()

    def on_browse_input(self, event):
        """Open a file dialog to select the input file."""
        with wx.FileDialog(self, "Select Input File", wildcard="CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_OK:
                self.input_text.SetValue(file_dialog.GetPath())

    def on_browse_output(self, event):
        """Open a file dialog to select the output file."""
        with wx.FileDialog(self, "Select Output File", wildcard="CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_OK:
                self.output_text.SetValue(file_dialog.GetPath())

    def on_transform(self, event):
        """Perform the transformation operation."""
        selected_description = self.operation_combo.GetValue()
        operation = next(key for key, value in VALID_OPERATIONS.items() if value == selected_description)
        input_file = self.input_text.GetValue()
        output_file = self.output_text.GetValue()

        # Validate input and output fields
        if not input_file:
            wx.MessageBox("Please select an input file.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not output_file:
            wx.MessageBox("Please select an output file.", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            # Call the transform_channels function
            transform_channels(operation, input_file, output_file, DEFAULT_START_CHANNEL)
            # Show success notification
            wx.MessageBox(f"Transformation successful!\nInput File: {input_file}\nOutput File: {output_file}",
                          "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            # Show error notification
            wx.MessageBox(f"An error occurred during transformation:\n{e}", "Error", wx.OK | wx.ICON_ERROR)


if __name__ == "__main__":
    app = wx.App(False)
    frame = FileConverterApp(None)
    frame.Show()
    app.MainLoop()
