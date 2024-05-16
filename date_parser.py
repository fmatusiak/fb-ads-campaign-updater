from dateutil import parser


class DateParser:
    @staticmethod
    def parseToDateTime(date):
        try:
            formatted_date = parser.parse(date).strftime('%Y-%m-%dT%H:%M:%S+0200')
            return formatted_date
        except ValueError as e:
            raise Exception('Wystąpił błąd z parsowaniem daty (start_time, stop_time)', e)
