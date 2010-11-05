"""
Configuration Class 
"""


import ConfigParser


class Config():
    """Configuration Class"""
    def __init__(self, file, section):
        """Constructor

        Args:
            file
            section

        Returns:
            Configuration parameters
        """
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(file))
        self.section = section

    def get(self, key, type="string"):
        """Retrieve configuration values

        Args:
            key
            type (optional)
        """
        if type == "int":
            return self.config.getint(self.section, key)
        elif type == "bool":
            return self.config.getboolean(self.section, key)
        else:
            return self.config.get(self.section, key)
