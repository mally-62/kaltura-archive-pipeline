import time
import logging

# Internal - our own config.py, no install needed
from config import (
    PARTNER_ID,
    ADMIN_SECRET,
    SERVICE_URL,
    SESSION_DURATION,
) #our config.py file

# Kaltura official Python client - pip install KalturaApiClient
from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.Plugins.Core import KalturaSessionType

# Logger
logger = logging.getLogger(__name__)

class KalturaAuth: 

    def __init__(self):
        self._client    = None  # KalturaClient instance
        self._ks_expiry = 0     # timestamp of when current token expires

    # Public
    def get_client(self) -> KalturaClient:
        # The only method the rest of the project calls
        # Returns a ready-to-use authenticated KalturaClient
        # Automatically refreshes the session if it is close to expiring
        if self._client is None:
            self._client = self._build_client()

        if self._is_expired():
            self._start_session()

        return self._client

    # Private
    def _build_client(self) -> KalturaClient:
        # Creates the KalturaClient instance with the service URL
        # Does not authenticate - just builds the connection object
        settings = KalturaConfiguration()
        settings.serviceUrl = SERVICE_URL
        return KalturaClient(settings)

    def _is_expired(self) -> bool:
        # Returns True if the current token is expired or about to expire
        # 5 minute buffer (300s) prevents mid-request token cutoffs
        return time.time() >= (self._ks_expiry - 300)

    def _start_session(self):
        # Authenticates with Kaltura and stores the new token on the client
        # Called automatically by get_client() - never call this directly
        try:
            ks = self._client.session.start(
                ADMIN_SECRET,
                "",                      # userId - empty means admin identity
                KalturaSessionType.ADMIN,
                PARTNER_ID,
                SESSION_DURATION,
                "disableentitlement",    # bypasses content restrictions
            )
            self._client.setKs(ks)
            self._ks_expiry = time.time() + SESSION_DURATION
            logger.info("Kaltura session started - valid for %ds", SESSION_DURATION)

        except Exception as e:
            logger.error("Failed to start Kaltura session: %s", e)
            raise