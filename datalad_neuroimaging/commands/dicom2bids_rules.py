"""Rule set for specification of DICOM image series
"""

# TODO: should include series_is_valid()!

# define specification keywords of specification type 'dicomseries', that are
# subjects to the rule set
keywords = ['description', 'comment', 'subject', 'session', 'task', 'run',
            'modality', 'converter', 'id']


def get_rules_from_metadata(dicommetadata):
    """Get the rules to apply

    Given a list of DICOM metadata dictionaries, determine which rule set to 
    apply (i.e. apply different rule set for different scanners).
    Note: This might need to change to the entire dict, datalad's dicom metadata 
    extractor delivers.

    Parameter:
    ----------
    dicommetadata: list of dict
        dicom metadata as extracted by datalad; one dict per image series

    Returns
    -------
    list of rule set classes
        wil be applied in order, therefore later ones overrule earlier ones
    """

    return [DefaultRules]


class DefaultRules(object):

    def __init__(self, dicommetadata):
        """
        
        Parameter
        ----------
        dicommetadata: list of dict
            dicom metadata as extracted by datalad; one dict per image series
        """
        self._dicoms = dicommetadata
        self.runs = dict()

    def __call__(self):
        spec_dicts = []
        for dicom_dict in self._dicoms:
            spec_dicts.append(self._rules(dicom_dict))
        return spec_dicts

    def _rules(self, record):

        if record['ProtocolName'] in self.runs:
            self.runs[record['ProtocolName']] += 1
        else:
            self.runs[record['ProtocolName']] = 1

        return {
                'description': record['SeriesDescription'],
                'comment': '',
                'subject': apply_bids_label_restrictions(record['PatientName']),
                'session': apply_bids_label_restrictions(record['ProtocolName']),
                'task': apply_bids_label_restrictions(record['ProtocolName']),
                'run': self.runs[record['ProtocolName']],
                # TODO: BIDS-conform modality; (func, anat, dwi, fmap):
                'modality': '',
                'id': record['SeriesNumber'],
                }


def apply_bids_label_restrictions(value):
    """
    Sanitize filenames for BIDS.
    """
    # only alphanumeric allowed
    # => remove everthing else

    import re
    pattern = re.compile('[\W_]+')  # check
    return pattern.sub('', value)


