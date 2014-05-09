workon benpledge_ve
../manage.py dumpdata publicweb --exclude publicweb.hatresultsdatabase --exclude publicweb.houseidlookup --exclude publicweb.lsoadomesticenergyconsumption --exclude publicweb.postcodeoalookup --exclude publicweb.pledge --exclude publicweb.ecoeligible --format json --indent 4 > ../publicweb/fixtures/publicweb_test_fixture.json
../manage.py dump_test_fixtures
../manage.py dumpdata auth > ../publicweb/fixtures/auth.json