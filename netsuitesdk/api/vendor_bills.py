import logging

from netsuitesdk.internal.utils import PaginatedSearch

from .base import ApiBase
from typing import List
from collections import OrderedDict

logger = logging.getLogger(__name__)

class VendorBills(ApiBase):
    """
    VendorBills are not directly searchable - only via as transactions
    """
    def __init__(self, ns_client):
        ApiBase.__init__(self, ns_client=ns_client, type_name='vendorBill')
    
    def get_all(self) -> List[OrderedDict]:
        record_type_search_field = self.ns_client.SearchStringField(searchValue='VendorBill', operator='contains')
        basic_search = self.ns_client.basic_search_factory('Transaction', recordType=record_type_search_field)
        paginated_search = PaginatedSearch(client=self.ns_client,
                                        type_name='Transaction',
                                        basic_search=basic_search,
                                        pageSize=20)
        # TODO: go over all the pages
        return self._serialize_array(paginated_search.records)
    
    def post(self, data) -> OrderedDict:
        assert data['externalId'], 'missing external id'
        vb = self.ns_client.VendorBill(externalId=data['externalId'])
        expense_list = []
        for eod in data['expenseList']:
            vbe = self.ns_client.VendorBillExpense(**eod)
            expense_list.append(vbe)
        
        vb['expenseList'] = self.ns_client.VendorBillExpenseList(expense=expense_list)
        vb['currency'] = self.ns_client.RecordRef(**(data['currency']))
        vb['memo'] = data['memo']
        vb['class'] = self.ns_client.RecordRef(**(data['class']))
        vb['location'] = self.ns_client.RecordRef(**(data['location']))
        vb['entity'] = self.ns_client.RecordRef(**(data['entity']))
        logger.debug('able to create vb = %s', vb)
        res = self.ns_client.upsert(vb)
        return self._serialize(res)