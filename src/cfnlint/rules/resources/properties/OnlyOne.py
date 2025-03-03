"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class OnlyOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""

    id = "E2523"
    shortdesc = "Check Properties that need only one of a list of properties"
    description = (
        "Making sure CloudFormation properties "
        + "that require only one property from a list. "
        + "One has to be specified."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super().__init__()
        onlyonespec = cfnlint.helpers.load_resource(AdditionalSpecs, "OnlyOne.json")
        self.resource_types_specs = onlyonespec["ResourceTypes"]
        self.property_types_specs = onlyonespec["PropertyTypes"]
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, onlyoneprops, path, cfn):
        """Check itself"""
        matches = []

        for onlyoneprop in onlyoneprops:
            for (safe_properties, safe_path) in properties.items_safe(path):
                property_sets = cfn.get_object_without_conditions(
                    safe_properties, onlyoneprop
                )
                for property_set in property_sets:
                    count = 0
                    for prop in onlyoneprop:
                        if prop in property_set["Object"]:
                            count += 1

                    if count != 1:
                        if property_set["Scenario"] is None:
                            message = "Only one of [{0}] should be specified for {1}"
                            matches.append(
                                RuleMatch(
                                    path,
                                    message.format(
                                        ", ".join(map(str, onlyoneprop)),
                                        "/".join(map(str, safe_path)),
                                    ),
                                )
                            )
                        else:
                            scenario_text = " and ".join(
                                [
                                    f'when condition "{k}" is {v}'
                                    for (k, v) in property_set["Scenario"].items()
                                ]
                            )
                            message = "Only one of [{0}] should be specified {1} at {2}"
                            matches.append(
                                RuleMatch(
                                    path,
                                    message.format(
                                        ", ".join(map(str, onlyoneprop)),
                                        scenario_text,
                                        "/".join(map(str, safe_path)),
                                    ),
                                )
                            )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        onlyoneprops = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, onlyoneprops, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        onlyoneprops = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, onlyoneprops, path, cfn))

        return matches
