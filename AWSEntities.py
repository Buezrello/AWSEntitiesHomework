class AwsObj:
    """
    Base class, not suppose to be instantiated
    """

    def __init__(self):
        """
        Instead of creating fields for every attribute
        this solution places all attributes to single dictionary as keys.
        It gives us more flexibility
        """
        self.dict_attr = dict()

    def _parse_string_dict(self, string):
        """
        parsing AWS string,
        convert the string to dictionary

        :param string: AWS string
        :return: dictionary that contains all required attributes
        """
        return dict(x.split(':') for x in string.split(','))

    def __to_string(self):
        """
        help function for str and repr
        represent object by class name and key:value pairs of dict_attr

        :return: string representation of object
        """
        cls = self.__class__.__name__
        key_values = []
        for k, v in self.dict_attr.items():
            key_values.append(' : '.join((k, v)))
        attributes = ' , '.join(key_values)
        return '{}({})'.format(cls, attributes)

    def __str__(self):
        return self.__to_string()

    def __repr__(self):
        return self.__to_string()


class AWSInstance(AwsObj):
    """
    represent AWS instance
    """

    def __init__(self, string):
        AwsObj.__init__(self)
        self.dict_attr = self._parse_string_dict(string)


class AWSVolume(AwsObj):
    """
    represent AWS volume
    """

    def __init__(self, string):
        AwsObj.__init__(self)
        self.dict_attr = self._parse_string_dict(string)


class AWSSnapshot(AwsObj):
    """
    represent AWS snapshot
    """

    def __init__(self, string):
        AwsObj.__init__(self)
        self.dict_attr = self._parse_string_dict(string)


def parse_aws_data(aws_type, data_str):
    """
    Parsing data string, creating list of AWS objects by given type
    If type incorrect return empty list

    :param aws_type: type of AWS object
    :param data_str: string represent AWS entities
    :return: list of AWS objects or Empty List
    """
    switch = {
        'instance': list(AWSInstance(x) for x in data_str.split('%') if x.strip() != ''),
        'volume': list(AWSVolume(x) for x in data_str.split('%') if x.strip() != ''),
        'snapshot': list(AWSSnapshot(x) for x in data_str.split('%') if x.strip() != '')
    }
    return switch.get(aws_type, [])


def dict_is_subset_of_dict(aws_obj, property_dict):
    """
    Create not empty dictionary if values in dict_attr of aws_obj
    and in property_dict don't match.
    If property_dict contains incorrect key aws_obj.dict_attr return None
    (instead of raising exception)
    Method return boolean ('not non-empty dict' is 'true' )

    :param aws_obj: object of AwsObj type
    :param property_dict: lookup dictionary
    :return: true if property_dict is subset of dict_attr
    """
    return not dict((key, val) for key, val in property_dict.items() if aws_obj.dict_attr.get(key) != val)


def aws_lookup(aws_obj_list, property_dict):
    """
    Return sub-list of AWS objects by property_dict criteria
    or empty list if no matches found

    :param aws_obj_list: list of AWS objects
    :param property_dict: criteria
    :return: sub-list of aws_obj_list
    """
    return list(aws_obj for aws_obj in aws_obj_list if dict_is_subset_of_dict(aws_obj, property_dict))


if __name__ == '__main__':
    aws_instance_data = 'id:1100,name:micro,state:running,region:oregon%' \
                        'id:1200,name:large1,state:terminated,region:n.virginia%' \
                        'id:1300,name:xlarge3,state:stopped,region:pasific%' \
                        'id:1400,name:large1,state:running,region:oregon'

    aws_volume_data = 'id:2100,name:data1,state:available,region:ohio,attached_instance_id:%' \
                      'id:2200,name:data1,state:in-use,region:ohio,attached_instance_id:1100%' \
                      'id:2300,name:data2,state:available,region:london,attached_instance_id:%' \
                      'id:2400,name:data2,state:in-use,region:oregon,attached_instance_id:1300'

    aws_snapshot_data = 'id:3100,name:data1_backup,region:oregon,source_volume_id:2100%' \
                        'id:3200,name:data2_backup,region:virginia,source_volume_id:2400%'

    aws_instance_obj_list = parse_aws_data('instance', aws_instance_data)
    aws_volume_obj_list = parse_aws_data('volume', aws_volume_data)
    aws_snapshot_obj_list = parse_aws_data(aws_type='snapshot', data_str=aws_snapshot_data)
    # incorrect type, returns empty list, for testing purposes only
    aws_mistake_obj_list = parse_aws_data('mistake', aws_snapshot_data)

    # printing all created objects in all lists
    # for testing purpose only
    print ('\nall created instance objects')
    for inst in aws_instance_obj_list:
        print (inst)

    print ('\nall created volume objects')
    for vol in aws_volume_obj_list:
        print (vol)

    print ('\nall created snapshot objects')
    for snap in aws_snapshot_obj_list:
        print (snap)

    print ('\nempty list print nothing')
    for mistake in aws_mistake_obj_list:
        print (mistake)

    available_volumes = aws_lookup(aws_volume_obj_list, property_dict={'state': 'available'})
    available_volumes_ohio = aws_lookup(aws_volume_obj_list, property_dict={'region': 'ohio', 'state': 'available'})
    running_instances_oregon = aws_lookup(aws_instance_obj_list, property_dict={'state': 'running', 'region': 'oregon'})
    # incorrect region, returns empty list
    empty_snapshot_list = aws_lookup(aws_snapshot_obj_list, property_dict={'region': 'incorrect'})
    # incorrect attribute, returns empty list
    empty_volumes_list = aws_lookup(aws_volume_obj_list, property_dict={'incorrect_attribute': 'paris'})

    print ('\navailable volumes list')
    for avail_vol in available_volumes:
        print (avail_vol)

    print ('\navailable in Ohio volumes list')
    for avail_ohio_vol in available_volumes_ohio:
        print (avail_ohio_vol)

    print ('\nrunning in Oregon instances list')
    for run_oregon in running_instances_oregon:
        print (run_oregon)

    print ('\nempty snapshot list, printing nothing')
    for empty_snapshot in empty_snapshot_list:
        print (empty_snapshot)

    print ('\nempty volumes list, printing nothing')
    for empty_volumes in empty_volumes_list:
        print (empty_volumes)

    # All volumes attached to running instances
    running_instances = aws_lookup(aws_instance_obj_list, property_dict={'state': 'running'})
    running_instances_volumes_dict = {}
    for single_running_instance in running_instances:
        instance_volumes_list = aws_lookup(aws_volume_obj_list,
                                           property_dict={'attached_instance_id': single_running_instance.dict_attr['id']})
        running_instances_volumes_dict[single_running_instance] = instance_volumes_list
    print ('\nAll volumes attached to running instances')
    for key in running_instances_volumes_dict:
        print (key)
        for single_volume in running_instances_volumes_dict[key]:
            print ('\t{}'.format(single_volume))
        if not running_instances_volumes_dict[key]:
            print ('\t{}'.format('No attached volumes'))

    # All not terminated instances
    terminated_instances = aws_lookup(aws_instance_obj_list,
                                      property_dict={'state': 'terminated'})
    print ('\nAll NOT terminated instances')
    for instance in list(set(aws_instance_obj_list) - set(terminated_instances)):
        print (instance)
