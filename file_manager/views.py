from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
import io
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def index(request):
    return render(request, 'index.html')

#File upload and validation:



def upload_file(request):
    if request.method == 'POST':  # Handle POST request for file upload
        excel_file = request.FILES.get('file')

        # Check if file exists
        if not excel_file:
            return JsonResponse({'error': 'No file uploaded. Please upload a valid Excel file.'}, status=400)

        # Check file extension
        if not excel_file.name.endswith(('.xls', '.xlsx')):
            return JsonResponse({'error': 'Invalid file format. Please upload an Excel file.'}, status=400)

        try:
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(excel_file)

            # Get column names
            columns = df.columns.tolist()

            # Save the DataFrame to session for later operations
            request.session['dataframe'] = df.to_dict()

            # Return column names in the response
            return JsonResponse({'columns': columns})

        except Exception as e:
            # Handle errors during file processing
            return JsonResponse({'error': f"An error occurred while processing the file: {str(e)}"}, status=400)
    
    else:
        # Handle non-POST requests
        return JsonResponse({'error': 'Invalid request method. Please use POST to upload a file.'}, status=405)


#Perform operation:


@csrf_exempt
def perform_operation(request):
    if request.method == 'POST':
      
        df = pd.DataFrame(request.session.get('dataframe', {}))
        body = json.loads(request.body)
        operation = body.get('operation')
        params = body.get('params', {})

        try:
            if operation == 'add_column':
                new_col = params['new_column_name']
                cols_to_sum = params['columns_to_sum']
                df[new_col] = df[cols_to_sum[0]] + df[cols_to_sum[1]]
            elif operation == 'combine_columns':
                new_col = params['new_column_name']
                cols_to_sum = params['columns_to_sum']
                df[new_col] = df[cols_to_sum[0]].astype(str) + ' ' + df[cols_to_sum[1]].astype(str)
            else:
                return JsonResponse({'error': 'Invalid operation.'}, status=400)

            request.session['dataframe'] = df.to_dict()  # Save updated dataframe
            preview = df.head().to_dict(orient='records')
            return JsonResponse({'columns': df.columns.tolist(), 'preview': preview})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

#Download file:

from django.http import HttpResponse
import io

def download_file(request):
    df = pd.DataFrame(request.session.get('dataframe', {}))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="updated_file.xlsx"'
    return response


