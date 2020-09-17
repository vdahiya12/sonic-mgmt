import logging
import random
import re
import time

import pytest
import yaml

from tests.common.helpers.assertions import pytest_assert
from tests.common.helpers.platform_api import chassis, thermal

from platform_api_test_base import PlatformApiTestBase

###################################################
# TODO: Remove this after we transition to Python 3
import sys
if sys.version_info.major == 3:
    STRING_TYPE = str
else:
    STRING_TYPE = basestring
# END Remove this after we transition to Python 3
###################################################

logger = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.disable_loganalyzer,  # disable automatic loganalyzer
    pytest.mark.topology('any')
]

@pytest.fixture(scope="class")
def gather_facts(request, duthost):
    # Get thermal truths from platform.json file
    chassis_truth = duthost.facts.get("chassis")
    if chassis_truth:
        request.cls.thermal_truth = chassis_truth.get('thermals', None)
        if not request.cls.thermal_truth:
            logger.warning("Unable to get thermal_truth from platform.json, test results will not be comprehensive")
    else:
        logger.warning("Unable to get chassis_truth from platform.json, test results will not be comprehensive")

    # Get host vars from inventory file
    request.cls.duthost_vars = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars


class TestThermalApi(PlatformApiTestBase):

    num_thermals = None
    thermal_truth = None
    duthost_vars = None

    # This fixture would probably be better scoped at the class level, but
    # it relies on the platform_api_conn fixture, which is scoped at the function
    # level, so we must do the same here to prevent a scope mismatch.

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, platform_api_conn):
        if self.num_thermals is None:
            try:
                self.num_thermals = int(chassis.get_num_thermals(platform_api_conn))
            except:
                pytest.fail("num_thermals is not an integer")

    #
    # Helper functions
    #

    def compare_value_with_platform_facts(self, key, value, i):
        expected_value = None

        if self.thermal_truth[i]:
            expected_value = self.thermal_truth[i].get(key)

        if not expected_value:
            logger.warning("Unable to get expected value for '{}' from platform.json file for thermal {}".format(key, i))
            return

        self.expect(value == expected_value,
                      "'{}' value is incorrect. Got '{}', expected '{}' for thermal {}".format(key, value, expected_value, i))


    #
    # Functions to test methods inherited from DeviceBase class
    #
    def test_get_name(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            name = thermal.get_name(platform_api_conn, i)

            if self.expect(name is not None, "Unable to retrieve Thermal {} name".format(i)):
                self.expect(isinstance(name, STRING_TYPE), "Thermal {} name appears incorrect".format(i))
                self.compare_value_with_platform_facts('name', name, i)

        self.assert_expectations()

    def test_get_presence(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            presence = thermal.get_presence(platform_api_conn, i)

            if self.expect(presence is not None, "Unable to retrieve thermal {} presence".format(i)):
                if self.expect(isinstance(presence, bool), "Thermal {} presence appears incorrect".format(i)):
                    self.expect(presence is True, "Thermal {} is not present".format(i))

        self.assert_expectations()

    def test_get_model(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            model = thermal.get_model(platform_api_conn, i)

            if self.expect(model is not None, "Unable to retrieve thermal {} model".format(i)):
                self.expect(isinstance(model, STRING_TYPE), "Thermal {} model appears incorrect".format(i))

        self.assert_expectations()

    def test_get_serial(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            serial = thermal.get_serial(platform_api_conn, i)

            if self.expect(serial is not None, "Unable to retrieve thermal {} serial number".format(i)):
                self.expect(isinstance(serial, STRING_TYPE), "Thermal {} serial number appears incorrect".format(i))

        self.assert_expectations()

    def test_get_status(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            status = thermal.get_status(platform_api_conn, i)

            if self.expect(status is not None, "Unable to retrieve thermal {} status".format(i)):
                self.expect(isinstance(status, bool), "Thermal {} status appears incorrect".format(i))

        self.assert_expectations()

    #
    # Functions to test methods defined in ThermalBase class
    #

    def test_get_temperature(self, duthost, localhost, platform_api_conn):
        for i in range(self.num_thermals):
            temperature = thermal.get_temperature(platform_api_conn, i)

            if self.expect(temperature is not None, "Unable to retrieve Thermal {} temperature".format(i)):
                if self.expect(isinstance(temperature, float), "Thermal {} temperature appears incorrect".format(i)):
                    self.expect(temperature > 0 and temperature <= 100,
                                "Thermal {} temperature {} reading is not within range".format(i, temperature))
        self.assert_expectations()

    def test_get_low_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal low threshold temperature is sane
        for i in range(self.num_thermals):
            low_threshold = thermal.get_low_threshold(platform_api_conn, i)

            if self.expect(low_threshold is not None, "Unable to retrieve Thermal {} low threshold".format(i)):
                if self.expect(isinstance(low_threshold, float), "Thermal {} low threshold appears incorrect".format(i)):
                    self.expect(low_threshold > 0 and low_threshold <= 100,
                                "Thermal {} low threshold {} reading is not within range".format(i, low_threshold))
                    self.compare_value_with_platform_facts('low_threshold', low_threshold, i)
        self.assert_expectations()

    def test_get_high_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal high threshold temperature is sane
        for i in range(self.num_thermals):
            high_threshold = thermal.get_high_threshold(platform_api_conn, i)

            if self.expect(high_threshold is not None, "Unable to retrieve Thermal {} high threshold".format(i)):
                if self.expect(isinstance(high_threshold, float), "Thermal {} high threshold appears incorrect".format(i)):
                    self.expect(high_threshold > 0 and high_threshold <= 100,
                                "Thermal {} high threshold {} reading is not within range".format(i, high_threshold))
                    self.compare_value_with_platform_facts('high_threshold', high_threshold, i)
        self.assert_expectations()

    def test_get_low_critical_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal low critical threshold temperature is sane
        for i in range(self.num_thermals):
            low_critical_threshold = thermal.get_low_critical_threshold(platform_api_conn, i)

            if self.expect(low_critical_threshold is not None, "Unable to retrieve Thermal {} low critical threshold".format(i)):
                if self.expect(isinstance(low_critical_threshold, float), "Thermal {} low threshold appears incorrect".format(i)):
                    self.expect(low_critical_threshold > 0 and low_critical_threshold <= 110,
                                "Thermal {} low critical threshold {} reading is not within range".format(i, low_critical_threshold))
                    self.compare_value_with_platform_facts('low_critical_threshold', low_critical_threshold, i)
        self.assert_expectations()

    def test_get_high_critical_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal high threshold temperature is sane
        for i in range(self.num_thermals):
            high_critical_threshold = thermal.get_high_critical_threshold(platform_api_conn, i)

            if self.expect(high_critical_threshold is not None, "Unable to retrieve Thermal {} high critical threshold".format(i)):
                if self.expect(isinstance(high_critical_threshold, float), "Thermal {} high threshold appears incorrect".format(i)):
                    self.expect(high_critical_threshold > 0 and high_critical_threshold <= 110,
                                "Thermal {} high critical threshold {} reading is not within range".format(i, high_critical_threshold))
                    self.compare_value_with_platform_facts('high_critical_threshold', high_critical_threshold, i)
        self.assert_expectations()

    def test_set_low_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal temperature is sane
        for i in range(self.num_thermals):
            low_temperature = 20
            result = thermal.set_low_threshold(platform_api_conn, i, low_temperature)
            if self.expect(result is not None, "Failed to perform set_low_threshold"):
                self.expect(result is True, "Failed to set set_low_threshold for thermal {} to {}".format(i, low_temperature))

            temperature = thermal.get_low_threshold(platform_api_conn, i)
            if self.expect(temperature is not None, "Unable to retrieve Thermal {} low threshold".format(i)):
                if self.expect(isinstance(temperature, float), "Thermal {} low threshold appears incorrect".format(i)):
                    self.expect(temperature == 20,
                                "Thermal {} low threshold {} is not matching the set value {}".format(i, temperature, low_temperature))

        self.assert_expectations()

    def test_set_high_threshold(self, duthost, localhost, platform_api_conn):
        # Ensure the thermal temperature is sane
        for i in range(self.num_thermals):
            high_temperature = 80
            result = thermal.set_high_threshold(platform_api_conn, i, high_temperature)
            if self.expect(result is not None, "Failed to perform set_high_threshold"):
                self.expect(result is True, "Failed to set set_high_threshold for thermal {} to {}".format(i, high_temperature))

            temperature = thermal.get_high_threshold(platform_api_conn, i)
            if self.expect(temperature is not None, "Unable to retrieve Thermal {} high threshold".format(i)):
                if self.expect(isinstance(temperature, float), "Thermal {} high threshold appears incorrect".format(i)):
                    self.expect(temperature == 80,
                                "Thermal {} high threshold {} is not matching the set value {}".format(i, temperature, high_temperature))
        self.assert_expectations()
