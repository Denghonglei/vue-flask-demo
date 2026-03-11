export const handler = async (event, context) => {
  console.log('Test function invoked!');
  console.log('Event:', JSON.stringify(event, null, 2));

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({
      success: true,
      message: 'Test function working!',
      path: event.path,
      headers: event.headers
    })
  };
};
