import time
import base64
import random
import argparse

import grpc

import lab6_pb2
import lab6_pb2_grpc


def doRawImage(stub, debug=False):

    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()

    response = stub.RawImage(lab6_pb2.rawImageMsg(img=img))

    if debug:
        print("Response is", response)

def doAdd(stub, debug=False):

    response = stub.Add(lab6_pb2.addMsg(a=5, b=10))

    if debug:
        print("Response is", response)

def doDotProduct(stub, debug=False):

    a = [random.random() for i in range(100)]
    b = [random.random() for i in range(100)]

    response = stub.DotProduct(lab6_pb2.dotProductMsg(a=a, b=b))

    if debug:
        print("Response is", response)

def doJsonImage(stub, debug=False):

    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    base64Img = base64.b64encode(img).decode('utf-8')

    response = stub.JsonImage(lab6_pb2.jsonImageMsg(img=base64Img))

    if debug:
        print("Response is", response)


parser = argparse.ArgumentParser(
    description='gRPC client for measuring server operations'
)

parser.add_argument(
    'host',
    help='IP address or hostname of the gRPC server'
)

parser.add_argument(
    'cmd',
    choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
    help='Operation to perform'
)

parser.add_argument(
    'reps',
    type=int,
    help='Number of repetitions for measurement'
)

parser.add_argument(
    '-p', '--port',
    type=int,
    default=50051,
    help='Server port (default: 50051)'
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Print the response from the server'
)

args = parser.parse_args()

# Build Channel & stub
addr = f"{args.host}:{args.port}"

channel = grpc.insecure_channel(addr)
stub = lab6_pb2_grpc.Lab6Stub(channel)

print(f"Running {args.reps} reps against {addr}")

# Perform Operation
ops = {
    'add': doAdd,
    'rawImage': doRawImage,
    'dotProduct': doDotProduct,
    'jsonImage': doJsonImage,
}

op = ops[args.cmd]

start = time.perf_counter()

for x in range(args.reps):
    op(stub, debug=args.debug)

delta = ((time.perf_counter() - start) / args.reps) * 1000
print("Took", delta, "ms per operation")

channel.close()