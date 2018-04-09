"""Rule set for specification of DICOM image series
"""

# TODO: should include series_is_valid()!

# define specification keywords of specification type 'dicomseries', that are
# subjects to the rule set
keywords = ['description', 'comment', 'subject', 'session', 'task', 'run',
            'modality', 'converter', 'id']


def series_is_valid(series):
    # filter "Series" entries from dataset metadata here, in order to get rid of
    # things, that aren't relevant image series
    # Those series are supposed to be ignored during conversion.
    # TODO: RF: integrate with rules definition

    # Note:
    # In 3T_visloc, SeriesNumber 0 is associated with ProtocolNames
    # 'DEFAULT PRESENTATION STATE' and 'ExamCard'.
    # All other SeriesNumbers have 1:1 relation to ProtocolNames and have 3-4
    # digits.
    # In 7T_ad there is no SeriesNumber 0 and the SeriesNumber doesn't have a 1:1
    # relation to ProtocolNames
    # Note: There also is a SeriesNumber 99 with protocol name 'Phoenix Document'?

    # Philips 3T Achieva
    if series['SeriesNumber'] == 0 and \
                    series['ProtocolName'] in ['DEFAULT PRESENTATION STATE',
                                               'ExamCard']:
        return False
    return True


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

        protocol_name = record.get('ProtocolName', None)
        if protocol_name in self.runs:
            self.runs[protocol_name] += 1
        else:
            self.runs[protocol_name] = 1

        return {
                'description': record['SeriesDescription'],
                'comment': '',
                'subject': apply_bids_label_restrictions(record.get('PatientName', None)),
                'session': apply_bids_label_restrictions(protocol_name),
                'task': apply_bids_label_restrictions(protocol_name),
                'run': self.runs[protocol_name],
                # TODO: BIDS-conform modality; (func, anat, dwi, fmap):
                'modality': '',
                'id': record.get('SeriesNumber', None),
                }


def apply_bids_label_restrictions(value):
    """
    Sanitize filenames for BIDS.
    """
    # only alphanumeric allowed
    # => remove everthing else

    from six import string_types
    if not isinstance(value, string_types):
        value = str(value)

    import re
    pattern = re.compile('[\W_]+')  # check
    return pattern.sub('', value)


